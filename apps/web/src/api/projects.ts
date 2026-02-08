import { get, post, del } from './client'
import type { Project } from '../types'

/** Fetch all projects */
export async function fetchProjects(): Promise<Project[]> {
  return get<Project[]>('/projects')
}

/** Fetch a single project */
export async function fetchProject(id: number): Promise<Project> {
  return get<Project>(`/projects/${id}`)
}

/** Create a new project */
export async function createProject(data: { name: string; description?: string }): Promise<Project> {
  return post<Project>('/projects', data)
}

/** Delete a project */
export async function deleteProject(id: number): Promise<void> {
  return del(`/projects/${id}`)
}
