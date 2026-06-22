// Mirrors core/schemas/reference.py and core/schemas/recommendation.py exactly.
// Keep in sync with the backend -- these are not independently-sourced types.

export type District = { code: string; name_en: string; is_disadvantaged: boolean };
export type Stream = {
  code: string;
  name_en: string;
  description: string | null;
  subjects: string[];
};
export type University = { code: string; name_en: string; short_name: string | null };

export type ReferenceData = {
  districts: District[];
  streams: Stream[];
  universities: University[];
};

export type SubjectInput = { subject: string; grade: "S" | "C" | "B" | "A" };

export type DimensionBreakdownItem = {
  name: string;
  weight: number;
  raw_score: number;
  contribution: number;
};

export type ScoredRecommendation = {
  course_code: string;
  course_name: string;
  university_code: string;
  university_name: string;
  cutoff_z_score: number;
  student_margin: number;
  selection_basis: string;
  requires_aptitude_test: boolean;
  status: "eligible" | "conditional";
  is_marginal: boolean;
  available_mediums: string[];
  total_score: number;
  bucket: "safe" | "ambitious" | "consider";
  breakdown: DimensionBreakdownItem[];
};

export type AlsoOfferedItem = {
  course_code: string;
  course_name: string;
  university_code: string;
  university_name: string;
  reason: string;
};

export type RecommendationResponse = {
  exam_year_used: number;
  confidence_tier: "current" | "previous_year" | "estimated";
  confidence_message: string | null;
  mode: "preference" | "normal";
  eligible_count: number;
  conditional_count: number;
  subject_filtered_count: number;
  bucket_counts: Record<string, number>;
  recommendations: ScoredRecommendation[];
  also_offered_no_cutoff_count: number;
  also_offered_no_cutoff: AlsoOfferedItem[];
};

export type RecommendationRequest = {
  z_score: number;
  district_code: string;
  stream_code: string;
  subjects: SubjectInput[];
  preferred_university_codes: string[];
  interests: string | null;
};
