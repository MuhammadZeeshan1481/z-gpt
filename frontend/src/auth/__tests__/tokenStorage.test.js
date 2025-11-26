import { TOKENS_CHANGED_EVENT, clearTokens, setTokens } from "../tokenStorage";

describe("tokenStorage events", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("emits an event when tokens are stored", () => {
    const listener = jest.fn();
    window.addEventListener(TOKENS_CHANGED_EVENT, listener);

    setTokens({ access_token: "abc", refresh_token: "def" });

    expect(listener).toHaveBeenCalledTimes(1);
    expect(listener.mock.calls[0][0].detail).toEqual({ access_token: "abc", refresh_token: "def" });

    window.removeEventListener(TOKENS_CHANGED_EVENT, listener);
  });

  it("emits an event when tokens are cleared", () => {
    const listener = jest.fn();
    window.addEventListener(TOKENS_CHANGED_EVENT, listener);

    clearTokens();

    expect(listener).toHaveBeenCalledTimes(1);
    expect(listener.mock.calls[0][0].detail).toBeNull();

    window.removeEventListener(TOKENS_CHANGED_EVENT, listener);
  });
});
