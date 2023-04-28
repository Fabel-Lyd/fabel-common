from typing import Dict, List, Optional
from fabelcommon.feed.import_service.import_status import ImportStatus
from fabelcommon.feed.import_service.import_result_item import ImportResultItem


class ImportResult:

    def __init__(self, import_report: List[Dict]) -> None:
        self.status: ImportStatus = self.__read_import_status(import_report[0]['sumOfStatuses'])
        self.created_items: List[ImportResultItem] = self.__read_created_items(import_report)
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
    def __read_created_items(import_report: List[Dict]) -> List[ImportResultItem]:
        created_items: List[ImportResultItem] = []

        for page in import_report:
            report_page_details: Optional[Dict] = page.get("report")

            if report_page_details is None:
                continue

            for item in report_page_details['content']:
                created_items.append(
                    ImportResultItem(
                        import_code=item['importCode'],
                        product_number=item['productNo']
                    )
                )

        return created_items

    @staticmethod
    def __create_report(import_report: List[Dict]) -> Dict:
        imported_items: int = import_report[0]['sumOfStatuses']['OK'] + import_report[0]['sumOfStatuses']['WARNING']
        total_items: int = imported_items + import_report[0]['sumOfStatuses']['ERROR']

        import_report_details: List[Dict] = []
        for page in import_report:
            page_details: Optional[List[Dict]] = page.get('report', {}).get('content')
            if page_details is not None:
                import_report_details += page_details

        return {
            'imported': f'{imported_items}/{total_items}',
            'details': import_report_details if len(import_report_details) > 0 else None
        }
