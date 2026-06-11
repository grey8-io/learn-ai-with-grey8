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

  it("offers a badge download, a LinkedIn link, and a GitHub fallback", () => {
    render(<CourseCompleteModal open onClose={() => {}} />);

    // Download the badge image itself (same-origin → forces a save).
    const download = screen.getByRole("link", { name: /download badge/i });
    expect(download).toHaveAttribute("href", "/badges/course-complete.png");
    expect(download).toHaveAttribute("download");

    // Open LinkedIn to compose the post manually.
    const linkedin = screen.getByRole("link", { name: /open linkedin/i });
    expect(linkedin.getAttribute("href") ?? "").toContain("linkedin.com");
    expect(linkedin).toHaveAttribute("target", "_blank");
    expect(linkedin).toHaveAttribute("rel", expect.stringContaining("noopener"));

    // Off-box fallback: grab the image straight from the public repo.
    const github = screen.getByRole("link", { name: /github/i });
    expect(github.getAttribute("href") ?? "").toContain(
      "grey8-io/learn-ai-with-grey8"
    );
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
