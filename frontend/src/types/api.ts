export interface Idea {
  headline: string;
  thesis: string;
  key_facts: string[];
  suggested_visualization: string;
}

export interface IdeasResponse {
  topic: string;
  num_ideas: number;
  ideas: Idea[];
  source_nodes?: SourceNode[];
  warning?: string;
}

export interface SourceNode {
  text: string;
  metadata: Record<string, unknown>;
  relevance_score?: number;
}

export interface Source {
  title: string;
  source: string;
  source_type: string;
  date: string;
  url: string;
  relevance_score?: number;
  text: string;
  citation_number?: number;
}

export interface OutlineRequest {
  headline: string;
  thesis: string;
  key_facts: string[];
  suggested_visualization?: string;
  enable_web_search?: boolean;
}

export interface OutlineResponse {
  headline: string;
  thesis: string;
  key_facts?: string[];
  suggested_visualization?: string;
  outline: string;
  sources?: Source[];
  warning?: string;
}

export interface DraftRequest {
  headline: string;
  thesis: string;
  outline: string;
  sources?: Source[];
  key_facts?: string[];
  target_word_count?: number;
  enable_web_search?: boolean;
}

export interface DraftResponse {
  headline: string;
  thesis: string;
  draft: string;
  word_count: number;
  sources_used?: Source[];
  sources_available?: Source[];
  sections_generated?: string[];
  editorial_compliance_score?: number;
  warning?: string;
}
