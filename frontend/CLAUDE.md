# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **frontend** of the AI Journalist Assistant - a React + TypeScript + Vite application that provides a workflow-oriented interface for journalists to generate article ideas, outlines, and drafts. The frontend is part of a larger full-stack application that includes a Python FastAPI backend (located in the parent directory).

**Design Philosophy**: Simple, clean components without over-engineering. Uses native browser APIs where possible. Professional interface designed for working journalists.

## Tech Stack

- **React 18** with TypeScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Icon library
- No state management library (uses React's built-in useState)
- No routing library (single-page workflow with conditional rendering)

## Development Commands

```bash
# Start development server (runs on http://localhost:5173)
pnpm  dev

# Type check without emitting files
pnpm typecheck

# Lint code
pnpm lint

# Build for production
pnpm build

# Preview production build locally
pnpm preview
```

## Environment Setup

The application requires a `.env` file with the API backend URL:

```bash
VITE_API_BASE_URL=http://localhost:8000  # For local development
# Or for production:
VITE_API_BASE_URL=https://your-api-url.com
```

See `.env.example` for reference.

## Architecture Overview

### Application Flow

The app uses a **step-based workflow** without routing - all managed through React state in `App.tsx`:

1. **Ideas Step** (`IdeaGeneration.tsx`)
   - User enters topic and number of ideas
   - Calls `/api/v1/ideas` endpoint
   - Displays generated ideas with sources
   - User selects an idea → advances to Outline

2. **Outline Step** (`OutlineGeneration.tsx`)
   - Pre-filled with selected idea data
   - Calls `/api/v1/outlines` endpoint
   - Displays structured outline with sources (both archive and web)
   - User generates outline → advances to Draft

3. **Draft Step** (`DraftGeneration.tsx`)
   - Pre-filled with outline data
   - Calls `/api/v1/drafts` endpoint
   - Displays full draft with citations
   - Provides copy/export functionality

### State Management Strategy

**No global state management library.** State is managed locally in `App.tsx` and passed down:

```typescript
// App.tsx manages workflow state
const [step, setStep] = useState<Step>('ideas');
const [selectedIdea, setSelectedIdea] = useState<Idea | null>(null);
const [generatedOutline, setGeneratedOutline] = useState<OutlineResponse | null>(null);
```

Each component manages its own UI state (loading, errors, form values) using `useState`.

### API Integration

All API calls are centralized in `src/services/api.ts`:

- `generateIdeas(topic, numIdeas)` - POST `/api/v1/ideas`
- `generateOutline(request)` - POST `/api/v1/outlines`
- `generateDraft(request)` - POST `/api/v1/drafts`

**API Communication**:
- Uses native `fetch` API (no axios)
- Base URL configured via `VITE_API_BASE_URL` environment variable
- Error handling done at component level
- Type-safe interfaces in `src/types/api.ts`

### Type System

All API contracts are defined in `src/types/api.ts`:
- Request/Response types for each endpoint
- Shared types like `Idea`, `Source`, `OutlineResponse`, `DraftResponse`
- Ensures type safety across components and API calls

## Component Structure

```
src/
├── components/
│   ├── Header.tsx              # App header with branding
│   ├── IdeaGeneration.tsx      # Step 1: Generate ideas
│   ├── IdeaCard.tsx            # Individual idea card display
│   ├── OutlineGeneration.tsx   # Step 2: Generate outline
│   └── DraftGeneration.tsx     # Step 3: Generate draft
├── services/
│   └── api.ts                  # All API calls
├── types/
│   └── api.ts                  # TypeScript interfaces
├── App.tsx                     # Main app with workflow logic
├── main.tsx                    # React entry point
└── index.css                   # Tailwind imports + custom styles
```

## Styling Approach

**Tailwind CSS with minimal custom CSS:**
- Brand colors: `#980000` (primary red), `#FFF4F3` (cream background)
- Uses utility classes directly in components
- Custom styles in `index.css` for global animations and gradients
- Responsive design with Tailwind breakpoints (`sm:`, `md:`, `lg:`)

**No component libraries** - all UI elements are custom built.

## Key Implementation Details

### API Base URL Handling

The API base URL defaults to empty string for same-origin requests:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
```

This allows the frontend to work with:
- Local development: `VITE_API_BASE_URL=http://localhost:8000`
- Production with proxy: No env var needed (same origin)
- Production with different domain: `VITE_API_BASE_URL=https://api.example.com`

### TypeScript Configuration

Three tsconfig files for different purposes:
- `tsconfig.json` - Base config
- `tsconfig.app.json` - App-specific compilation settings
- `tsconfig.node.json` - Node/build tool settings (Vite config)

Use `npm run typecheck` to verify types without building.

### Vite Configuration

Located at `vite.config.ts`:
- Optimizes lucide-react separately (excluded from pre-bundling)
- Standard React plugin configuration
- Hot module replacement enabled by default

## Development Guidelines

1. **Keep components simple** - Avoid unnecessary abstractions
2. **Colocate state** - Keep state close to where it's used
3. **Use TypeScript strictly** - All props and state should be typed
4. **Native APIs first** - Use browser APIs before adding libraries
5. **Tailwind utilities** - Style directly with utilities, avoid custom classes
6. **Error boundaries** - Handle API errors at component level, not globally

## Backend Integration

The frontend expects the following backend API structure:

- Backend is a FastAPI Python application (in parent directory)
- Uses LlamaIndex with ReActAgent for multi-source retrieval
- Qdrant vector database for archive articles
- Tavily API for real-time web search
- OpenAI API for LLM operations

**Backend must be running** for frontend to work. See parent directory's CLAUDE.md for backend setup.

## Building for Production

```bash
npm run build
```

Output directory: `dist/`

The build:
- Compiles TypeScript to JavaScript
- Bundles all assets with Vite
- Optimizes for production (minification, tree-shaking)
- Can be served by any static file server

## Testing Strategy

Currently no automated tests. Manual testing workflow:
1. Start backend API server
2. Start frontend dev server
3. Test full workflow: Ideas → Outline → Draft
4. Verify API integration and error states
