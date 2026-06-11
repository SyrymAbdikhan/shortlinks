from httpx import AsyncClient

TARGET_URL = "https://example.com/page"


async def _create(client: AsyncClient, auth_headers: dict, url: str = TARGET_URL) -> dict:
    r = await client.post("/links", json={"url": url}, headers=auth_headers)
    return r.json()


class TestCreateLink:
    async def test_success(self, client: AsyncClient, auth_headers: dict) -> None:
        response = await client.post("/links", json={"url": TARGET_URL}, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert len(data["code"]) == 6
        assert data["url"] == TARGET_URL
        assert "created_at" in data

    async def test_missing_api_key(self, client: AsyncClient) -> None:
        response = await client.post("/links", json={"url": TARGET_URL})
        assert response.status_code == 401

    async def test_wrong_api_key(self, client: AsyncClient) -> None:
        bad_headers = {"X-API-Key": "wrong"}
        response = await client.post("/links", json={"url": TARGET_URL}, headers=bad_headers)
        assert response.status_code == 401

    async def test_invalid_url(self, client: AsyncClient, auth_headers: dict) -> None:
        response = await client.post("/links", json={"url": "not-a-url"}, headers=auth_headers)
        assert response.status_code == 422

    async def test_codes_are_unique(self, client: AsyncClient, auth_headers: dict) -> None:
        r1 = await client.post("/links", json={"url": TARGET_URL}, headers=auth_headers)
        r2 = await client.post("/links", json={"url": TARGET_URL}, headers=auth_headers)
        assert r1.json()["code"] != r2.json()["code"]


class TestRedirect:
    async def test_redirects_to_original_url(self, client: AsyncClient, auth_headers: dict) -> None:
        code = (await _create(client, auth_headers))["code"]
        response = await client.get(f"/{code}", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == TARGET_URL

    async def test_not_found(self, client: AsyncClient) -> None:
        response = await client.get("/xxxxxx")
        assert response.status_code == 404


class TestListLinks:
    async def test_empty(self, client: AsyncClient) -> None:
        response = await client.get("/links")
        assert response.status_code == 200
        assert response.json() == []

    async def test_returns_all_created(self, client: AsyncClient, auth_headers: dict) -> None:
        await _create(client, auth_headers, "https://example.com/a")
        await _create(client, auth_headers, "https://example.com/b")
        response = await client.get("/links")
        assert response.status_code == 200
        assert len(response.json()) == 2

    async def test_no_auth_required(self, client: AsyncClient) -> None:
        response = await client.get("/links")
        assert response.status_code == 200


class TestDeleteLink:
    async def test_success(self, client: AsyncClient, auth_headers: dict) -> None:
        code = (await _create(client, auth_headers))["code"]
        response = await client.delete(f"/links/{code}", headers=auth_headers)
        assert response.status_code == 204

    async def test_deleted_link_is_gone(self, client: AsyncClient, auth_headers: dict) -> None:
        code = (await _create(client, auth_headers))["code"]
        await client.delete(f"/links/{code}", headers=auth_headers)
        assert (await client.get(f"/{code}")).status_code == 404

    async def test_not_found(self, client: AsyncClient, auth_headers: dict) -> None:
        response = await client.delete("/links/xxxxxx", headers=auth_headers)
        assert response.status_code == 404

    async def test_missing_api_key(self, client: AsyncClient, auth_headers: dict) -> None:
        code = (await _create(client, auth_headers))["code"]
        response = await client.delete(f"/links/{code}")
        assert response.status_code == 401
