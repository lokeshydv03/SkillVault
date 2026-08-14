export interface Skill {
  id: string;
  name: string;
  slug: string;
  description: string;
  capability: string;
  category: string;
  status: "DRAFT" | "ACTIVE" | "DEPRECATED" | "ARCHIVED";
  source_type: "BUILTIN" | "GENERATED" | "IMPORTED";
  created_by: "SYSTEM" | "AGENT" | "USER";
  risk_level: "TRUSTED" | "LOW" | "MEDIUM" | "HIGH" | "UNTRUSTED";
  input_schema: Record<string, any>;
  output_schema: Record<string, any>;
  dependencies: string[];
  active_version_id?: string | null;
  usage_count: number;
  success_count: number;
  failure_count: number;
  success_rate: number;
  last_used_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface SkillVersion {
  id: string;
  skill_id: string;
  version: string;
  code: string;
  language: string;
  entrypoint: string;
  description?: string | null;
  input_schema: Record<string, any>;
  output_schema: Record<string, any>;
  dependencies: string[];
  created_at: string;
}

export interface SkillSearchResult {
  skill_id: string;
  name: string;
  slug: string;
  description: string;
  capability: string;
  score: number;
  semantic_score: number;
  reliability_score: number;
  success_rate: number;
  status: string;
  source_type: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface SkillGenerateResponse {
  status: "DRAFT_CREATED" | "VALIDATION_FAILED";
  skill: {
    id?: string;
    name: string;
    slug: string;
    source_type?: string;
    status?: string;
    version?: string;
  };
  validation: ValidationResult;
}

export interface Task {
  id: string;
  user_input: string;
  normalized_task?: string | null;
  status: "pending" | "analyzing" | "retrieving" | "executing" | "completed" | "failed";
  strategy?: "reuse" | "generate" | null;
  retrieval_trace?: Record<string, any> | null;
  result?: Record<string, any> | null;
  error?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskExecutionResponse {
  task_id: string;
  status: string;
  strategy: "reuse" | "generate";
  skill?: {
    skill_id: string;
    name: string;
    slug: string;
    description: string;
    capability: string;
    score: number;
    semantic_score?: number;
    reliability_score?: number;
    status: string;
    source_type: string;
  } | null;
  execution?: {
    status: string;
    output_data?: Record<string, any>;
    error?: string | null;
    latency_ms: number;
  } | null;
  result?: Record<string, any> | null;
  error?: string | null;
}

export interface Execution {
  id: string;
  task_id: string;
  skill_id?: string | null;
  skill_version_id?: string | null;
  strategy: "REUSE" | "GENERATE";
  status: "SUCCESS" | "FAILED" | "DRAFT_SAVED" | "NOT_EXECUTED" | "PENDING";
  retrieval_score?: number | null;
  latency_ms: number;
  input_data: Record<string, any>;
  output_data?: Record<string, any> | null;
  error?: string | null;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}
