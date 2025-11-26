import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ChatBox from "../ChatBox";
import { useOnlineStatus } from "../../hooks/useOnlineStatus";
import { sendMessage, listSessions } from "../../api/chat";

jest.mock("../../api/chat", () => ({
  deleteSession: jest.fn(),
  getSessionDetail: jest.fn(),
  listSessions: jest.fn(),
  sendMessage: jest.fn(),
}));

jest.mock("../../api/image", () => ({
  generateImage: jest.fn().mockResolvedValue("fake"),
}));

jest.mock("../../hooks/useOnlineStatus", () => ({
  useOnlineStatus: jest.fn(),
}));

const mockOnline = (value) => {
  useOnlineStatus.mockReturnValue(value);
};

describe("ChatBox", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    listSessions.mockResolvedValue([]);
    mockOnline(true);
  });

  it("shows offline banner when offline", async () => {
    mockOnline(false);
    render(<ChatBox forceSync />);

    await waitFor(() => expect(listSessions).toHaveBeenCalled());
    expect(screen.getByRole("status")).toHaveTextContent(/offline/i);
  });

  it("sends a message via sync fallback when streaming disabled", async () => {
    sendMessage.mockResolvedValue({ response: "Hi there", detected_lang: "en", session_id: "abc" });
    render(<ChatBox forceSync />);

    await waitFor(() => expect(listSessions).toHaveBeenCalled());

    await userEvent.type(screen.getByPlaceholderText(/type your message/i), "Hello");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => expect(sendMessage).toHaveBeenCalled());
    expect(screen.getByText(/Hi there/)).toBeInTheDocument();
  });

  it("filters session list based on search query", async () => {
    listSessions.mockResolvedValue([
      { id: "1", title: "Project Alpha", updated_at: new Date().toISOString(), last_message_preview: "Alpha" },
      { id: "2", title: "Weekend Plans", updated_at: new Date().toISOString(), last_message_preview: "Plans" },
    ]);
    render(<ChatBox forceSync />);

    await waitFor(() => expect(screen.getByText(/project alpha/i)).toBeInTheDocument());

    await userEvent.type(screen.getByLabelText(/search chat sessions/i), "weekend");
    expect(screen.queryByText(/project alpha/i)).not.toBeInTheDocument();
    expect(screen.getByText(/weekend plans/i)).toBeInTheDocument();
  });
});
