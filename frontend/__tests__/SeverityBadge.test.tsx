import { render, screen } from "@testing-library/react";
import SeverityBadge from "@/components/ui/SeverityBadge";

describe("SeverityBadge", () => {
  it("renders critical badge", () => {
    render(<SeverityBadge severity="critical" />);
    expect(screen.getByText("critical")).toBeInTheDocument();
  });

  it("renders high badge", () => {
    render(<SeverityBadge severity="high" />);
    expect(screen.getByText("high")).toBeInTheDocument();
  });

  it("renders medium badge with correct class", () => {
    const { container } = render(<SeverityBadge severity="medium" />);
    expect(container.firstChild).toHaveClass("bg-yellow-100");
  });

  it("renders low badge", () => {
    render(<SeverityBadge severity="low" />);
    expect(screen.getByText("low")).toBeInTheDocument();
  });
});
