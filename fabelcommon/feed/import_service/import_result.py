from typing import Dict, List, Optional
from fabelcommon.feed.import_service.import_status import ImportStatus
from fabelcommon.feed.import_service.import_result_item import ImportResultItem


class ImportResult:

    def __init__(self, import_report: Dict) -> None:
        self.status: ImportStatus = self.__read_import_status(import_report['sumOfStatuses'])
        self.created_items: List[ImportResultItem] = self.__read_created_items(import_report.get('report'))
        self.report: Dict = self.__create_report(import_report)

    @staticmethod
    def __read_import_status(status_summary: Dict) -> ImportStatus:
        if status_summary['ERROR'] != 0:
            return ImportStatus.ERROR
        elif status_summary['WARNING'] != 0:
            return ImportStatus.WARNING
        else:
            return ImportStatus.OK

    @staticmethod
    def __read_created_items(report_details: Optional[Dict]) -> List[ImportResultItem]:
        if report_details is None:
            return []

        created_items: List[ImportResultItem] = []

        for item in report_details['content']:
            created_items.append(
                ImportResultItem(
                    import_code=item['importCode'],
                    product_number=item['productNo']
                )
            )
        return created_items

    @staticmethod
    def __create_report(import_report: Dict) -> Dict:
        imported_items: int = import_report['sumOfStatuses']['OK'] + import_report['sumOfStatuses']['WARNING']
        total_items: int = imported_items + import_report['sumOfStatuses']['ERROR']

        return {
            'imported': f'{imported_items}/{total_items}',
            'details': import_report.get('report', {}).get('content')
        }
