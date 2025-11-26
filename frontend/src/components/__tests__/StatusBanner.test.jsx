import { render, screen } from "@testing-library/react";
import StatusBanner from "../ui/StatusBanner";

describe("StatusBanner", () => {
  it("shows offline warning when offline", () => {
    render(<StatusBanner online={false} streaming={false} loading={false} />);
    expect(screen.getByRole("status")).toHaveTextContent(/offline/i);
  });

  it("shows streaming message when active", () => {
    render(<StatusBanner online streaming loading={false} />);
    expect(screen.getByRole("status")).toHaveTextContent(/streaming response/i);
  });

  it("renders nothing when idle", () => {
    const { container } = render(<StatusBanner online streaming={false} loading={false} />);
    expect(container).toBeEmptyDOMElement();
  });
});
