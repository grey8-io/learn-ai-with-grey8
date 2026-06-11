import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import CourseCompleteCard from "../CourseCompleteCard";
import { fetchManifest } from "@/lib/api";

const mockGetAllLessonProgress = jest.fn();

jest.mock("@/components/ProgressProvider", () => ({
  useProgress: () => ({
    backend: { getAllLessonProgress: mockGetAllLessonProgress },
    isReady: true,
  }),
}));

jest.mock("@/lib/api", () => ({ fetchManifest: jest.fn() }));

jest.mock("next/image", () => ({
  __esModule: true,
  default: ({ src, alt }: { src: string; alt: string }) =>
    // eslint-disable-next-line @next/next/no-img-element
    <img src={typeof src === "string" ? src : ""} alt={alt} />,
}));

const MANIFEST = {
  phases: [
    { phase: 1, title: "P1", lessons: [{ id: "p1/l1" }, { id: "p1/l2" }] },
  ],
};

function progress(ids: string[]) {
  return ids.map((id) => ({ lessonId: id, status: "completed" }));
}

beforeEach(() => {
  jest.clearAllMocks();
  (fetchManifest as jest.Mock).mockResolvedValue(MANIFEST);
});

it("renders nothing until the course is fully complete", async () => {
  mockGetAllLessonProgress.mockResolvedValue(progress(["p1/l1"])); // 1 of 2
  const { container } = render(<CourseCompleteCard />);
  await waitFor(() => expect(fetchManifest).toHaveBeenCalled());
  expect(
    screen.queryByRole("link", { name: /share on linkedin/i })
  ).not.toBeInTheDocument();
  expect(container).toBeEmptyDOMElement();
});

it("shows a persistent share card once every lesson is complete", async () => {
  mockGetAllLessonProgress.mockResolvedValue(progress(["p1/l1", "p1/l2"]));
  render(<CourseCompleteCard />);

  const link = await screen.findByRole("link", { name: /share on linkedin/i });
  expect(decodeURIComponent(link.getAttribute("href") ?? "")).toContain(
    "github.com/grey8-io/learn-ai-with-grey8"
  );
  expect(link).toHaveAttribute("target", "_blank");
  expect(link).toHaveAttribute("rel", expect.stringContaining("noopener"));
  expect(screen.getByText(/completed the entire bootcamp/i)).toBeInTheDocument();
});

it("opens the full badge modal from 'View badge'", async () => {
  mockGetAllLessonProgress.mockResolvedValue(progress(["p1/l1", "p1/l2"]));
  render(<CourseCompleteCard />);

  fireEvent.click(await screen.findByText(/view badge/i));
  // Modal heading appears (distinct from the card's copy).
  expect(await screen.findByText(/Course Complete/i)).toBeInTheDocument();
});
