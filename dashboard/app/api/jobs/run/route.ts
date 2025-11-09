import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import prisma from '@/lib/prisma';

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);

    if (!session || session.user?.email !== process.env.OWNER_EMAIL) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 403 });
    }

    const body = await req.json();
    const { type, league } = body;

    if (!type || !league) {
      return NextResponse.json(
        { error: 'Missing required fields: type, league' },
        { status: 400 }
      );
    }

    // Create job record
    const job = await prisma.job.create({
      data: {
        type,
        league,
        status: 'pending',
        triggeredBy: session.user.email,
      },
    });

    // Log the action
    await prisma.auditLog.create({
      data: {
        userId: session.user.email,
        action: 'job_trigger',
        details: JSON.stringify({ jobId: job.id, type, league }),
        ipAddress: req.headers.get('x-forwarded-for') || 'unknown',
        userAgent: req.headers.get('user-agent') || 'unknown',
      },
    });

    // In a real implementation, you would trigger the actual AI pipeline here
    // For now, we'll simulate it by updating the job status after a delay
    setTimeout(async () => {
      await prisma.job.update({
        where: { id: job.id },
        data: {
          status: 'completed',
          result: JSON.stringify({
            message: 'Job completed successfully (simulated)',
            timestamp: new Date().toISOString(),
          }),
        },
      });
    }, 5000);

    return NextResponse.json({
      success: true,
      job: {
        id: job.id,
        type: job.type,
        league: job.league,
        status: job.status,
        createdAt: job.createdAt,
      },
    });
  } catch (error) {
    console.error('Error running job:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);

    if (!session || session.user?.email !== process.env.OWNER_EMAIL) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 403 });
    }

    // Get recent jobs
    const jobs = await prisma.job.findMany({
      orderBy: { createdAt: 'desc' },
      take: 50,
    });

    return NextResponse.json({ jobs });
  } catch (error) {
    console.error('Error fetching jobs:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
