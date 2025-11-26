import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import Login from "../Login";
import { useAuth } from "../../hooks/useAuth";

jest.mock("../../hooks/useAuth");

const mockNavigate = jest.fn();

jest.mock("react-router-dom", () => {
  const actual = jest.requireActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe("Login page", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useAuth.mockReturnValue({
      login: jest.fn(),
      isAuthenticated: false,
      loading: false,
    });
  });

  it("submits credentials and navigates", async () => {
    const loginMock = jest.fn().mockResolvedValue({});
    useAuth.mockReturnValue({ login: loginMock, isAuthenticated: false, loading: false });

    render(
      <MemoryRouter
        initialEntries={[{ pathname: "/login", state: { from: { pathname: "/image" } } }]}
      >
        <Login />
      </MemoryRouter>
    );

    await userEvent.type(screen.getByLabelText(/email/i), "user@example.com");
    await userEvent.type(screen.getByLabelText(/password/i), "secret123");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => expect(loginMock).toHaveBeenCalledWith({ email: "user@example.com", password: "secret123" }));
    expect(mockNavigate).toHaveBeenCalledWith("/image", { replace: true });
  });

  it("surfaces authentication errors", async () => {
    const loginMock = jest.fn().mockRejectedValue(new Error("Invalid credentials"));
    useAuth.mockReturnValue({ login: loginMock, isAuthenticated: false, loading: false });

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    await userEvent.type(screen.getByLabelText(/email/i), "user@example.com");
    await userEvent.type(screen.getByLabelText(/password/i), "secret123");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument());
  });
});
