#!/usr/bin/env bash
# ament_xmllint のスキーマ検証をオフラインで行うための設定。
#
# 各 package.xml の <?xml-model?> は
# http://download.ros.org/schema/package_format3.xsd を指しており、
# ament_xmllint はその URL をそのまま xmllint に渡す。libxml2 の HTTP
# 取得にはタイムアウトが無いため、ダウンロードが停止すると xmllint が
# ハングし、CTest の 60 秒タイムアウトでテストが失敗する。
#
# リポジトリに同梱した XML カタログを XML_CATALOG_FILES に登録して
# URL をローカルの .xsd に解決させ、ネットワークアクセスを無くす。
#
# 使い方（実行ではなく source する）:
#   source scripts/xml-catalog.sh

_xml_catalog_file="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/xml-schema/catalog.xml"

if [[ -f "${_xml_catalog_file}" ]]; then
  case " ${XML_CATALOG_FILES:-} " in
    *" ${_xml_catalog_file} "*)
      ;;
    *)
      # XML_CATALOG_FILES は空白区切り。未設定時はシステム既定の
      # /etc/xml/catalog も残しておく。
      export XML_CATALOG_FILES="${_xml_catalog_file} ${XML_CATALOG_FILES:-/etc/xml/catalog}"
      ;;
  esac
else
  echo "warning: ${_xml_catalog_file} が見つかりません。" \
    "xmllint がスキーマをネットワーク取得する可能性があります。" >&2
fi

unset _xml_catalog_file
