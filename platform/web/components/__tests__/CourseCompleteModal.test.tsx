import { render, screen, fireEvent } from "@testing-library/react";
import CourseCompleteModal from "../CourseCompleteModal";

// Stub next/image with a plain <img> so jsdom can assert on src/alt.
jest.mock("next/image", () => ({
  __esModule: true,
  default: ({ src, alt }: { src: string; alt: string }) =>
    // eslint-disable-next-line @next/next/no-img-element
    <img src={typeof src === "string" ? src : ""} alt={alt} />,
}));

describe("CourseCompleteModal", () => {
  it("renders nothing when closed", () => {
    const { container } = render(
      <CourseCompleteModal open={false} onClose={() => {}} />
    );
    expect(container).toBeEmptyDOMElement();
  });

  it("shows the finale badge and copy when open", () => {
    render(<CourseCompleteModal open onClose={() => {}} />);
    expect(screen.getByText(/Course Complete/i)).toBeInTheDocument();
    const badge = screen.getByAltText(/course completion badge/i);
    expect(badge).toHaveAttribute("src", "/badges/course-complete.png");
  });

  it("exposes a correct, safe LinkedIn share link", () => {
    render(<CourseCompleteModal open onClose={() => {}} />);
    const link = screen.getByRole("link", { name: /share on linkedin/i });
    const href = link.getAttribute("href") ?? "";
    expect(href).toContain("linkedin.com/sharing/share-offsite/");
    expect(decodeURIComponent(href)).toContain(
      "github.com/grey8-io/learn-ai-with-grey8"
    );
    // Opens in a new tab without leaking the opener (security).
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", expect.stringContaining("noopener"));
  });

  it("calls onClose from the Continue button, backdrop, and Escape", () => {
    const onClose = jest.fn();
    const { container } = render(
      <CourseCompleteModal open onClose={onClose} />
    );

    fireEvent.click(screen.getByText(/Continue/i));
    expect(onClose).toHaveBeenCalledTimes(1);

    // Backdrop is the first absolutely-positioned overlay div.
    const backdrop = container.querySelector(".absolute.inset-0");
    fireEvent.click(backdrop!);
    expect(onClose).toHaveBeenCalledTimes(2);

    fireEvent.keyDown(window, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(3);
  });
});
