export type ColorPattern = "green" | "yellow" | "gray";

export interface RowRequest {
  id: string;
  pattern: ColorPattern[];
}

export interface SolveOptions {
  max_candidates_per_row?: number;
  distinct_words_across_rows?: boolean;
}

export interface SolveRequestPayload {
  solution: string;
  rows: { id: string; pattern: ColorPattern[] }[];
  options?: SolveOptions;
}

export interface RowResult {
  id: string;
  pattern: ColorPattern[];
  candidate_count: number;
  candidates: string[];
  best_guess: string | null;
}

export interface SolveResponse {
  solution: string;
  word_length: number;
  rows: RowResult[];
  unsolvable_row_ids: string[];
}

export interface HealthResponse {
  status: string;
  library_size: number;
  word_length_distribution: Record<string, number>;
}

export interface MismatchDetail {
  index: number;
  expected: string;
  actual: string;
  letter: string;
}

export interface ValidateResponse {
  valid: boolean;
  is_real_word: boolean;
  computed_pattern: ColorPattern[] | null;
  mismatches: MismatchDetail[];
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8001";

export async function checkBackendHealth(): Promise<HealthResponse> {
  const res = await fetch(`${BACKEND_URL}/api/v1/health`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Health check failed with status ${res.status}`);
  }
  return res.json();
}

export async function solvePuzzle(payload: SolveRequestPayload): Promise<SolveResponse> {
  const res = await fetch(`${BACKEND_URL}/api/v1/puzzle/solve`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      solution: payload.solution,
      rows: payload.rows,
      options: {
        max_candidates_per_row: payload.options?.max_candidates_per_row ?? 20,
        distinct_words_across_rows: payload.options?.distinct_words_across_rows ?? true,
      },
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Solving failed" }));
    throw new Error(errorData.detail || "Failed to solve puzzle");
  }

  return res.json();
}

export async function validateGuess(
  guess: string,
  solution: string,
  target_pattern: ColorPattern[]
): Promise<ValidateResponse> {
  const res = await fetch(`${BACKEND_URL}/api/v1/guess/validate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ guess, solution, target_pattern }),
  });

  if (!res.ok) {
    throw new Error("Validation request failed");
  }

  return res.json();
}
