import { exportToGoogleDocs, exportToMarkdown } from './api';

export async function exportStoryToGoogleDocs(content: string, title: string): Promise<string> {
  try {
    const result = await exportToGoogleDocs(content, title);
    return result.docUrl;
  } catch (error) {
    console.error('Failed to export to Google Docs:', error);
    throw new Error('Failed to export to Google Docs');
  }
}

export async function downloadAsMarkdown(content: string, title: string): Promise<void> {
  try {
    const result = await exportToMarkdown(content, title);

    // Create a blob and download
    const blob = new Blob([result.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = result.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Failed to download markdown:', error);
    throw new Error('Failed to download markdown file');
  }
}

export function copyToClipboard(content: string): Promise<void> {
  return navigator.clipboard.writeText(content);
}
