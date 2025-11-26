import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders chat heading", () => {
  render(<App />);
  const heading = screen.getByRole("heading", { name: /Z-GPT Assistant/i });
  expect(heading).toBeInTheDocument();
});
