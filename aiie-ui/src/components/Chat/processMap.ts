export type ProcessName = 'title_generate' | 'llm' | 'tool';

const processMap: Record<ProcessName, string> = {
    title_generate: "Generating Title",
    llm: "Thinking",
    tool: "Processing Image",
}

export default processMap;