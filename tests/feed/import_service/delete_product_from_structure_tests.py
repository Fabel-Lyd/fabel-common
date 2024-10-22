import json
from typing import List
from unittest.mock import MagicMock
import pytest
from rest_framework import status
from fabelcommon.feed.import_service import FeedImport
from fabelcommon.feed.import_service.product_identifier import ProductIdentifier
from fabelcommon.feed.import_service.structure_node import StructureNode


def test_delete_product_from_structure(requests_mock) -> None:
    test_product_identifier_list: List[ProductIdentifier] = [
        ProductIdentifier(
            import_code=32781,
            product_number='9788234001635'
        ),
        ProductIdentifier(
            import_code=33279,
            product_number='9788241919312'
        )
    ]

    test_structure_node: StructureNode = StructureNode(
        structure_import_code='sjanger',
        node_import_code='barn-romaner-og-fortellinger'
    )

    requests_mock.post(
        url='https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )

    product_delete_call: MagicMock = requests_mock.delete(
        url='https://lydbokforlaget-feed.isysnet.no/import/structure/sjanger/node/barn-romaner-og-fortellinger/product',
        status_code=status.HTTP_204_NO_CONTENT,
    )
    feed_import: FeedImport = FeedImport('test_client_id', 'test_client_secret')
    feed_import.delete_product_from_structure(test_product_identifier_list, test_structure_node)

    assert product_delete_call.call_count == 1
    assert product_delete_call.last_request.text == '[{"productNo": "9788234001635"}, {"productNo": "9788241919312"}]'


def test_delete_product_from_structure_failure(requests_mock) -> None:
    test_product_identifier_list: List[ProductIdentifier] = [
        ProductIdentifier(
            import_code=32781,
            product_number='9788234001635'
        ),
        ProductIdentifier(
            import_code=33279,
            product_number='9788241919312'
        )
    ]
    test_structure_node: StructureNode = StructureNode(
        structure_import_code='sjanger',
        node_import_code='barn-romaner-og-fortellinger'
    )

    requests_mock.post(
        url='https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )

    requests_mock.delete(
        url='https://lydbokforlaget-feed.isysnet.no/import/structure/sjanger/node/barn-romaner-og-fortellinger/product',
        status_code=status.HTTP_404_NOT_FOUND,
        text=json.dumps({
            "type": "about:blank",
            "title": "Not Found",
            "status": 404,
            "detail": "No value present",
            "instance": "/import/structure/test-structure/node/romaner-og-fortellingr/product",
            "Warnings": None,
            "Body": [
                {
                    "productNo": "9788241919312",
                    "importCode": None,
                    "sortNo": None
                }
            ]
        }
        )
    )

    feed_import: FeedImport = FeedImport('test_client_id', 'test_client_secret')

    with pytest.raises(Exception) as exception:
        feed_import.delete_product_from_structure(test_product_identifier_list, test_structure_node)

    assert str(exception.value) == 'Error 404 calling https://lydbokforlaget-feed.isysnet.no/import/structure/sjanger/node/barn-romaner-og-fortellinger/product, details: {"type": "about:blank", "title": "Not Found", "status": 404, "detail": "No value present", "instance": "/import/structure/test-structure/node/romaner-og-fortellingr/product", "Warnings": null, "Body": [{"productNo": "9788241919312", "importCode": null, "sortNo": null}]}'
