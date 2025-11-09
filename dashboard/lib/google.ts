import { google } from 'googleapis';

/**
 * Google Drive/Docs Integration
 * Exports stories to Google Docs with proper formatting
 */

export interface GoogleExportOptions {
  title: string;
  content: string;
  league: string;
  type: string;
  date: Date;
}

export async function exportToGoogleDocs(options: GoogleExportOptions): Promise<string> {
  try {
    // Parse credentials from env
    const credentials = JSON.parse(process.env.GOOGLE_DRIVE_CREDENTIALS || '{}');

    if (!credentials.client_email || !credentials.private_key) {
      throw new Error('Invalid Google Drive credentials');
    }

    // Create JWT auth client
    const auth = new google.auth.JWT({
      email: credentials.client_email,
      key: credentials.private_key,
      scopes: [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/documents',
      ],
    });

    const drive = google.drive({ version: 'v3', auth });
    const docs = google.docs({ version: 'v1', auth });

    // Format: /Drive/{LEAGUE}/{TYPE}/{YYYY-MM-DD}/{TITLE}
    const dateStr = options.date.toISOString().split('T')[0];
    const rootFolderId = process.env.GOOGLE_ROOT_FOLDER_ID;

    // Create folder structure if needed
    let currentFolderId = rootFolderId;

    const folderPath = [options.league, options.type, dateStr];

    for (const folderName of folderPath) {
      const existingFolder = await drive.files.list({
        q: `name='${folderName}' and '${currentFolderId}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false`,
        fields: 'files(id, name)',
      });

      if (existingFolder.data.files && existingFolder.data.files.length > 0) {
        currentFolderId = existingFolder.data.files[0].id!;
      } else {
        const folder = await drive.files.create({
          requestBody: {
            name: folderName,
            mimeType: 'application/vnd.google-apps.folder',
            parents: [currentFolderId!],
          },
          fields: 'id',
        });
        currentFolderId = folder.data.id!;
      }
    }

    // Create the Google Doc
    const doc = await docs.documents.create({
      requestBody: {
        title: options.title,
      },
    });

    const documentId = doc.data.documentId!;

    // Move to correct folder
    await drive.files.update({
      fileId: documentId,
      addParents: currentFolderId!,
      removeParents: 'root',
      fields: 'id, parents',
    });

    // Insert content (convert markdown to Google Docs format)
    await docs.documents.batchUpdate({
      documentId,
      requestBody: {
        requests: [
          {
            insertText: {
              location: {
                index: 1,
              },
              text: options.content,
            },
          },
        ],
      },
    });

    // Return the document URL
    return `https://docs.google.com/document/d/${documentId}/edit`;
  } catch (error) {
    console.error('Error exporting to Google Docs:', error);
    throw error;
  }
}
