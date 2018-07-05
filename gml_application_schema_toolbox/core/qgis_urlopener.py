# -*- coding: utf-8 -*-

#   Copyright (C) 2016 BRGM (http:///brgm.fr)
#   Copyright (C) 2016 Oslandia <infos@oslandia.com>
#
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Library General Public
#   License as published by the Free Software Foundation; either
#   version 2 of the License, or (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Library General Public License for more details.
#   You should have received a copy of the GNU Library General Public
#   License along with this library; if not, see <http://www.gnu.org/licenses/>.

from builtins import str
from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode

from qgis.PyQt.QtCore import QUrl, QEventLoop
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkAccessManager
from io import BytesIO
from qgis.core import QgsNetworkAccessManager, QgsApplication

from gml_application_schema_toolbox.core.settings import settings
from gml_application_schema_toolbox import name as plugin_name

__network_manager = None

def _sync_get(url):
    global __network_manager
    if __network_manager is None:
        __network_manager = QNetworkAccessManager()
        __network_manager.setProxy(QgsNetworkAccessManager.instance().proxy())
    pause = QEventLoop()
    req = QNetworkRequest(url)

    authcfg = None
    url_str = url.url()
    if 'authcfg' in url_str.lower():
        # Grab authcfg, then strip it from URL
        url_p = urlparse(url_str)
        url_query = url_p.query.strip()
        params = parse_qsl(url_query, keep_blank_values=True)
        clean_params = []
        for k, v in params:
            if k.lower() == 'authcfg':
                authcfg = v
                continue
            clean_params.append((k, v))
        url_new_p = list(url_p)
        url_new_p[4] = urlencode(clean_params, doseq=True) \
            if clean_params else ''
        clean_url = urlunparse(url_new_p)
        url.setUrl(clean_url)

    if authcfg:  # avoid empty string value
        QgsApplication.instance().authManager().updateNetworkRequest(
            req, authcfg=authcfg)

    if req.url().scheme().lower() == 'https':
        # Merge in QGIS trusted CAs
        ssl_conf = req.sslConfiguration()
        ssl_conf.setCaCertificates(
            QgsApplication.instance().authManager().trustedCaCertsCache())
        req.setSslConfiguration(ssl_conf)

    req.setRawHeader(b"Accept", b"application/xml")
    req.setRawHeader(b"Accept-Language", bytes(settings.value("default_language", "fr"), "utf8"))
    req.setRawHeader(b"User-Agent", bytes(settings.value('http_user_agent', plugin_name()), "utf8"))
    reply = __network_manager.get(req)
    reply.finished.connect(pause.quit)
    is_ok = [True]
    def onError(self):
        is_ok[0] = False
        pause.quit()
    reply.error.connect(onError)
    pause.exec_()
    return reply, is_ok[0]

def remote_open_from_qgis(uri):
    """Opens a remote URL using QGIS proxy preferences"""
    reply, is_ok = _sync_get(QUrl.fromEncoded(bytes(uri, "utf8")))
    if not is_ok:
        raise RuntimeError("Network problem when downloading {}".format(uri))
    redirect = reply.attribute(QNetworkRequest.RedirectionTargetAttribute)
    # Handle HTTP 302 redirections
    while redirect is not None and not redirect.isEmpty():
        reply, is_ok = _sync_get(redirect)
        if not is_ok:
            raise RuntimeError("Network problem when downloading {}".format(uri))
        redirect = reply.attribute(QNetworkRequest.RedirectionTargetAttribute)
    r = bytes(reply.readAll())
    reply.close()
    return BytesIO(r)
