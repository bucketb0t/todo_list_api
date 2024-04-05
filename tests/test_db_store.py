from utils.db_store import ToDoDBStore
import pytest


class TestToDoDBStore:
    @pytest.fixture(scope="function")
    def mongo_driver(self):
        todo_db = ToDoDBStore()
        return todo_db

    @pytest.fixture(scope="function")
    def todo_document_fix(self):
        todo_pytest_0 = {
            "id": 0,
            "title": "PytestFixture",
            "description": "FirstInstance",
            "completed": True
        }

        todo_pytest_1 = {
            "id": 1,
            "title": "AnotherPytestFixture",
            "description": "SecondInstance",
            "completed": True
        }

        return [todo_pytest_0, todo_pytest_1]

    def test_add_todo(self, mongo_driver, todo_document_fix):
        mongo_driver.delete_all_documents("todo_list_db", "todo_list_collection", {})
        inserted_ids = []

        # Add each document in todo_document_fix
        for document_fix in todo_document_fix:
            result = mongo_driver.add_document("todo_list_db", "todo_list_collection", document_fix)
            inserted_ids.append(result.inserted_id)

        # Check if all documents were inserted successfully
        assert all(inserted_id is not None for inserted_id in inserted_ids)

        mongo_driver.delete_all_documents("todo_list_db", "todo_list_collection", {})

    def test_get_all_documents(self, mongo_driver, todo_document_fix):
        mongo_driver.delete_all_documents("todo_list_db", "todo_list_collection", {})

        # Add all documents to the database
        for document_fix in todo_document_fix:
            result = mongo_driver.add_document("todo_list_db", "todo_list_collection", document_fix)

        result = mongo_driver.get_all_documents("todo_list_db", "todo_list_collection")

        for document_fix in todo_document_fix:
            # Iterate over each document fix
            found = False
            for document in result:
                # Iterate over each document in the result
                if all(document[key] == value for key, value in document_fix.items()):
                    # Check if the document matches the document_fix
                    found = True
                    break
            assert found, f"Document matching {document_fix} not found in result"

        mongo_driver.delete_all_documents("todo_list_db", "todo_list_collection", {})

    def test_get_document_by_id(self, mongo_driver, todo_document_fix):
        mongo_driver.delete_all_documents("todo_list_db", "todo_list_collection", {})

        # Insert test documents
        for document_fix in todo_document_fix:
            mongo_driver.add_document("todo_list_db", "todo_list_collection", document_fix)

        # Retrieve document by id
        test_document_id = 1
        result = mongo_driver.get_document_by_id("todo_list_db", "todo_list_collection", test_document_id)

        # Check if the result is not None
        assert result is not None
        # Check if the retrieved document has the correct id
        assert result["id"] == test_document_id

        mongo_driver.delete_all_documents("todo_list_db", "todo_list_collection", {})

    def test_get_document_by_query(self, mongo_driver, todo_document_fix):
        mongo_driver.delete_all_documents("todo_list_db", "todo_list_collection", {})

        for document_fix in todo_document_fix:
            mongo_driver.add_document("todo_list_db", "todo_list_collection", document_fix)

        test_query = {"id": 1}

        # Retrieve document by query
        result = mongo_driver.get_document_by_query("todo_list_db", "todo_list_collection", test_query)

        assert result is not None

        # Find the corresponding document in todo_document_fix
        expected_document = next(item for item in todo_document_fix if item["id"] == 1)

        # Since result is a cursor, iterate over it to access the documents
        for document in result:
            # Compare each key-value pair in the expected document with the result
            for key, value in expected_document.items():
                assert document[key] == value

        mongo_driver.delete_all_documents("todo_list_db", "todo_list_collection", {})

    def test_update_document_by_id(self, mongo_driver, todo_document_fix):
        # Delete all documents in the collection
        mongo_driver.delete_all_documents("todo_list_db", "todo_list_collection", {})

        # Add documents to the collection
        for document_fix in todo_document_fix:
            mongo_driver.add_document("todo_list_db", "todo_list_collection", document_fix)

        # Update a document with id 1
        result = mongo_driver.update_document_by_id("todo_list_db", "todo_list_collection", 1,
                                                    {"title": "UpdatedAnotherPytestFixture"})

        assert result is not None
        assert result.modified_count == 1
        assert mongo_driver.get_document_by_id("todo_list_db", "todo_list_collection", 1)[
                   "title"] == "UpdatedAnotherPytestFixture"
