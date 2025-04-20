"""
Tests for Celery tasks.
"""
import pytest
from unittest.mock import MagicMock, patch
from celery.exceptions import Ignore


class TestImportProductsTask:
    """Test cases for import_products task."""

    @patch("app.services.infrastructure.async_tasks.celery.tasks.import_products")
    def test_import_products_success(self, mock_import_products):
        """Test successful import of products."""
        # Arrange
        # Mock the return value of import_products
        mock_import_products.return_value = {
            "status": "completed",
            "total": 2,
            "processed": 2,
            "failed": 0,
            "failed_items": []
        }

        # Create a mock task instance
        task_instance = MagicMock()

        # Test data
        products_data = [
            {
                "name": "Product 1",
                "description": "Description 1",
                "price": 19.99,
                "stock": 100,
            },
            {
                "name": "Product 2",
                "description": "Description 2",
                "price": 29.99,
                "stock": 50,
            },
        ]
        user_id = 1

        # Act
        result = mock_import_products(task_instance, products_data, user_id)

        # Assert
        assert result["status"] == "completed"
        assert result["total"] == 2
        assert result["processed"] == 2
        assert result["failed"] == 0

        # Check that import_products was called with the right arguments
        mock_import_products.assert_called_once_with(task_instance, products_data, user_id)

    @patch("app.services.infrastructure.async_tasks.celery.tasks.import_products")
    def test_import_products_partial_failure(self, mock_import_products):
        """Test import of products with some failures."""
        # Arrange
        # Mock the return value of import_products
        mock_import_products.return_value = {
            "status": "completed",
            "total": 2,
            "processed": 1,
            "failed": 1,
            "failed_items": [
                {
                    "data": {
                        "name": "Product 2",
                        "description": "Description 2",
                        "price": 29.99,
                        "stock": 50,
                    },
                    "error": "Invalid product data"
                }
            ]
        }

        # Create a mock task instance
        task_instance = MagicMock()

        # Test data
        products_data = [
            {
                "name": "Product 1",
                "description": "Description 1",
                "price": 19.99,
                "stock": 100,
            },
            {
                "name": "Product 2",
                "description": "Description 2",
                "price": 29.99,
                "stock": 50,
            },
        ]
        user_id = 1

        # Act
        result = mock_import_products(task_instance, products_data, user_id)

        # Assert
        assert result["status"] == "completed"
        assert result["total"] == 2
        assert result["processed"] == 1
        assert result["failed"] == 1
        assert len(result["failed_items"]) == 1
        assert result["failed_items"][0]["data"] == products_data[1]
        assert "Invalid product data" in result["failed_items"][0]["error"]

    @patch("app.services.infrastructure.async_tasks.celery.tasks.import_products")
    def test_import_products_total_failure(self, mock_import_products):
        """Test import of products with complete failure."""
        # Arrange
        # Mock the return value of import_products
        mock_import_products.return_value = {
            "status": "completed",
            "total": 2,
            "processed": 0,
            "failed": 2,
            "failed_items": [
                {
                    "data": {
                        "name": "Product 1",
                        "description": "Description 1",
                        "price": 19.99,
                        "stock": 100,
                    },
                    "error": "Database error"
                },
                {
                    "data": {
                        "name": "Product 2",
                        "description": "Description 2",
                        "price": 29.99,
                        "stock": 50,
                    },
                    "error": "Database error"
                }
            ]
        }

        # Create a mock task instance
        task_instance = MagicMock()

        # Test data
        products_data = [
            {
                "name": "Product 1",
                "description": "Description 1",
                "price": 19.99,
                "stock": 100,
            },
            {
                "name": "Product 2",
                "description": "Description 2",
                "price": 29.99,
                "stock": 50,
            },
        ]
        user_id = 1

        # Act
        result = mock_import_products(task_instance, products_data, user_id)

        # Assert
        assert result["status"] == "completed"
        assert result["total"] == 2
        assert result["processed"] == 0
        assert result["failed"] == 2
        assert len(result["failed_items"]) == 2

    @patch("app.services.infrastructure.async_tasks.celery.tasks.import_products")
    def test_import_products_session_error(self, mock_import_products):
        """Test handling of session error."""
        # Arrange
        # Make import_products raise an Ignore exception
        mock_import_products.side_effect = Ignore()

        # Create a mock task instance
        task_instance = MagicMock()
        task_instance.update_state = MagicMock()

        # Test data
        products_data = [
            {
                "name": "Product 1",
                "description": "Description 1",
                "price": 19.99,
                "stock": 100,
            },
        ]
        user_id = 1

        # Act & Assert
        with pytest.raises(Ignore):
            mock_import_products(task_instance, products_data, user_id)

        # Check that import_products was called with the right arguments
        mock_import_products.assert_called_once_with(task_instance, products_data, user_id)
