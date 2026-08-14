import axios from "axios";
import {
  Execution,
  PaginatedResponse,
  Skill,
  SkillGenerateResponse,
  SkillSearchResult,
  SkillVersion,
  Task,
  TaskExecutionResponse,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// System Health API
export async function getSystemHealth(): Promise<{ status: string; version: string; message: string }> {
  const response = await axios.get(`${API_BASE_URL}/`);
  return response.data;
}

// Skills API
export async function getSkills(params?: {
  status?: string;
  category?: string;
  name?: string;
  page?: number;
  limit?: number;
}): Promise<PaginatedResponse<Skill>> {
  const response = await apiClient.get("/skills", { params });
  return response.data;
}

export async function getSkillById(id: string): Promise<Skill> {
  const response = await apiClient.get(`/skills/${id}`);
  return response.data;
}

export async function getSkillVersions(skillId: string): Promise<SkillVersion[]> {
  const response = await apiClient.get(`/skills/${skillId}/versions`);
  return response.data;
}

export async function getSkillExecutions(skillId: string): Promise<Execution[]> {
  const response = await apiClient.get(`/skills/${skillId}/executions`);
  return response.data;
}

export async function searchSkills(query: string, topK: number = 5): Promise<SkillSearchResult[]> {
  const response = await apiClient.post("/skills/search", { query, top_k: topK });
  return response.data.results;
}

export async function generateSkill(task: string): Promise<SkillGenerateResponse> {
  const response = await apiClient.post("/skills/generate", { task });
  return response.data;
}

// Tasks & Agent Playground API
export async function submitTask(input: string): Promise<TaskExecutionResponse> {
  const response = await apiClient.post("/tasks", { input });
  return response.data;
}

export async function getTasks(page: number = 1, limit: number = 20): Promise<PaginatedResponse<Task>> {
  const response = await apiClient.get("/tasks", { params: { page, limit } });
  return response.data;
}

export async function getTaskById(taskId: string): Promise<Task> {
  const response = await apiClient.get(`/tasks/${taskId}`);
  return response.data;
}

// Executions API
export async function getExecutions(page: number = 1, limit: number = 20): Promise<PaginatedResponse<Execution>> {
  const response = await apiClient.get("/executions", { params: { page, limit } });
  return response.data;
}

export async function getExecutionById(executionId: string): Promise<Execution> {
  const response = await apiClient.get(`/executions/${executionId}`);
  return response.data;
}
