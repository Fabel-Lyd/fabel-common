from unittest.mock import MagicMock
import json
import pytest
from rest_framework import status
from fabelcommon.feed.import_service import FeedImport
from fabelcommon.feed.import_service.product_identifier import ProductIdentifier
from fabelcommon.feed.import_service.structure_node import StructureNode


def test_add_product_to_structure_success(requests_mock) -> None:
    test_product_identifier: ProductIdentifier = ProductIdentifier(
        import_code=32781,
        product_number='9788234001635'
    )
    test_structure_node: StructureNode = StructureNode(
        structure_import_code='sjanger',
        node_import_code='barn-romaner-og-fortellinger'
    )

    requests_mock.post(
        url='https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )

    product_add_call: MagicMock = requests_mock.post(
        url='https://lydbokforlaget-feed.isysnet.no/import/structure/sjanger/node/barn-romaner-og-fortellinger/product',
        status_code=status.HTTP_200_OK,
    )

    feed_import: FeedImport = FeedImport('test_client_id', 'test_client_secret')
    feed_import.add_product_to_structure(test_product_identifier, test_structure_node)

    assert product_add_call.call_count == 1
    assert product_add_call.last_request.text == '{"productNo": "9788234001635", "importCode": 32781}'


def test_add_product_to_structure_failure(requests_mock) -> None:
    test_product_identifier: ProductIdentifier = ProductIdentifier(
        import_code=32781,
        product_number='9788234001635'
    )
    test_structure_node: StructureNode = StructureNode(
        structure_import_code='sjanger',
        node_import_code='barn-romaner-og-fortellinger'
    )

    requests_mock.post(
        url='https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )

    requests_mock.post(
        url='https://lydbokforlaget-feed.isysnet.no/import/structure/sjanger/node/barn-romaner-og-fortellinger/product',
        status_code=status.HTTP_400_BAD_REQUEST,
        text=json.dumps({
            "type": "about:blank",
            "title": "Bad Request",
            "status": 400,
            "detail": "Unknown error",
            "instance": "/import/structure/3/node/33/product",
            "Warnings": {
                "WARNING_1": "warning text",
                "WARNING_2": "warning text"
            },
            "Body": [
                {
                    "productNo": "9788234001635",
                    "importCode": 32781,
                    "sortNo": None
                }
            ]
        })
    )

    feed_import: FeedImport = FeedImport('test_client_id', 'test_client_secret')

    with pytest.raises(Exception) as exception:
        feed_import.add_product_to_structure(test_product_identifier, test_structure_node)

    assert str(exception.value) == 'Error 400 calling https://lydbokforlaget-feed.isysnet.no/import/structure/sjanger/node/barn-romaner-og-fortellinger/product, details: {"type": "about:blank", "title": "Bad Request", "status": 400, "detail": "Unknown error", "instance": "/import/structure/3/node/33/product", "Warnings": {"WARNING_1": "warning text", "WARNING_2": "warning text"}, "Body": [{"productNo": "9788234001635", "importCode": 32781, "sortNo": null}]}'
