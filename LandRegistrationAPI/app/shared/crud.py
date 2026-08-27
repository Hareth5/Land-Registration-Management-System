from pymongo.errors import ConfigurationError, ConnectionFailure


class DatabaseUnavailableError(RuntimeError):
    """Raised when MongoDB cannot be reached."""


def _raise_crud_error(operation: str, error: Exception) -> None:
    if isinstance(error, (ConfigurationError, ConnectionFailure)):
        raise DatabaseUnavailableError(
            "MongoDB is unavailable or misconfigured. Verify MONGO_URI and the "
            "Atlas database user and IP access list."
        ) from error

    raise RuntimeError(f"CRUD {operation} Error: {error}") from error


def create(collection, document):

    try:

        result = collection.insert_one(document)

        return result.inserted_id

    except Exception as e:
        _raise_crud_error("Create", e)


def get_one(collection, filter_dict):

    try:

        return collection.find_one(filter_dict)

    except Exception as e:
        _raise_crud_error("Get One", e)


def get_many(
    collection,
    filter_dict: dict = None,
    skip: int = 0,
    limit: int = 100,
    sort_field: str = None,
    sort_order: int = 1,
):

    try:

        query = collection.find(filter_dict or {})

        if sort_field:

            query = query.sort(sort_field, sort_order)

        query = query.skip(skip).limit(limit)

        return list(query)

    except Exception as e:
        _raise_crud_error("Get Many", e)


def update_one(
    collection,
    filter_dict: dict,
    data: dict,
):

    try:

        result = collection.update_one(
            filter_dict,
            {"$set": data},
        )

        if result.matched_count == 0:

            return None

        return collection.find_one(filter_dict)

    except Exception as e:
        _raise_crud_error("Update", e)


def delete_one(
    collection,
    filter_dict: dict,
):

    try:

        document = collection.find_one(filter_dict)

        if not document:

            return None

        collection.delete_one(filter_dict)

        return document

    except Exception as e:
        _raise_crud_error("Delete", e)


def count(
    collection,
    filter_dict: dict = None,
):

    try:

        return collection.count_documents(filter_dict or {})

    except Exception as e:
        _raise_crud_error("Count", e)
