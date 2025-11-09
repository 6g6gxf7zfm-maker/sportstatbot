import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import prisma from '@/lib/prisma';
import { exportToAppleNotes } from '@/lib/apple';

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);

    if (!session || session.user?.email !== process.env.OWNER_EMAIL) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 403 });
    }

    const body = await req.json();
    const { title, content, league, storyType, folder, tags } = body;

    if (!title || !content || !league || !storyType) {
      return NextResponse.json(
        { error: 'Missing required fields: title, content, league, storyType' },
        { status: 400 }
      );
    }

    // Export to Apple Notes
    await exportToAppleNotes({
      title,
      body: content,
      folder: folder || `Sports/${league}`,
      tags: tags || [league, storyType],
    });

    // Record the export
    const exportRecord = await prisma.export.create({
      data: {
        type: 'apple_notes',
        title,
        league,
        storyType,
        exportedBy: session.user.email,
        metadata: JSON.stringify({
          contentLength: content.length,
          folder,
          tags,
        }),
      },
    });

    // Log the action
    await prisma.auditLog.create({
      data: {
        userId: session.user.email,
        action: 'export_apple_notes',
        details: JSON.stringify({ exportId: exportRecord.id, title, league }),
        ipAddress: req.headers.get('x-forwarded-for') || 'unknown',
        userAgent: req.headers.get('user-agent') || 'unknown',
      },
    });

    return NextResponse.json({
      success: true,
      export: {
        id: exportRecord.id,
        createdAt: exportRecord.createdAt,
      },
    });
  } catch (error) {
    console.error('Error exporting to Apple Notes:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
}
