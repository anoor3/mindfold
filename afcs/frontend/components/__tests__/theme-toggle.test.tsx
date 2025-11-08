import { fireEvent, render, screen } from "@testing-library/react";

import { ThemeProvider } from "../../components/theme-provider";
import { ThemeToggle } from "../../components/ThemeToggle";

function Wrapper() {
  return (
    <ThemeProvider>
      <ThemeToggle />
    </ThemeProvider>
  );
}

test("toggles theme", () => {
  render(<Wrapper />);
  const button = screen.getByRole("button", { name: /toggle theme/i });
  fireEvent.click(button);
  expect(document.documentElement.getAttribute("data-theme")).toBe("light");
});
