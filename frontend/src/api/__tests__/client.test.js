import { requestJson } from "../client";
import * as tokenStorage from "../../auth/tokenStorage";

const jsonResponse = (body, init = {}) =>
  new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
    ...init,
  });

const originalFetch = global.fetch;

describe("requestJson", () => {
  beforeEach(() => {
    jest.spyOn(tokenStorage, "setTokens").mockImplementation(() => {});
    jest.spyOn(tokenStorage, "clearTokens").mockImplementation(() => {});
    jest.spyOn(tokenStorage, "getRefreshToken").mockReturnValue("refresh-token");
    global.fetch = jest.fn();
  });

  afterEach(() => {
    global.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  it("retries the request after silently refreshing tokens", async () => {
    global.fetch
      .mockResolvedValueOnce(jsonResponse({ detail: { code: "unauthorized" } }, { status: 401 }))
      .mockResolvedValueOnce(jsonResponse({ access_token: "new", refresh_token: "new-refresh" }))
      .mockResolvedValueOnce(jsonResponse({ ok: true }));

    const result = await requestJson("/chat", {
      method: "POST",
      body: JSON.stringify({ message: "hi" }),
    });

    expect(global.fetch).toHaveBeenCalledTimes(3);
    expect(tokenStorage.setTokens).toHaveBeenCalledWith({ access_token: "new", refresh_token: "new-refresh" });
    expect(result).toEqual({ ok: true });
  });

  it("propagates the original error if refresh fails", async () => {
    global.fetch
      .mockResolvedValueOnce(jsonResponse({ detail: { code: "unauthorized" } }, { status: 401 }))
      .mockResolvedValueOnce(jsonResponse({ detail: { code: "refresh_failed" } }, { status: 400 }));

    await expect(
      requestJson("/chat", {
        method: "GET",
      })
    ).rejects.toThrow(/request/i);
    expect(tokenStorage.clearTokens).toHaveBeenCalled();
  });
});
