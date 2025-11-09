/**
 * Apple Notes Integration
 * Sends content to Apple Notes via Shortcuts webhook
 */

export interface AppleNotesExportOptions {
  title: string;
  body: string;
  folder?: string;
  tags?: string[];
}

export async function exportToAppleNotes(options: AppleNotesExportOptions): Promise<boolean> {
  try {
    const webhookUrl = process.env.APPLE_SHORTCUT_WEBHOOK;

    if (!webhookUrl) {
      throw new Error('Apple Shortcut webhook URL not configured');
    }

    const payload = {
      title: options.title,
      body: options.body,
      folder: options.folder || 'Sports Intelligence',
      tags: options.tags || [],
      timestamp: new Date().toISOString(),
    };

    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Apple Notes export failed: ${response.statusText}`);
    }

    return true;
  } catch (error) {
    console.error('Error exporting to Apple Notes:', error);
    throw error;
  }
}
