// Mock Prisma client for environments where Prisma binaries can't be downloaded
// This allows the app to run without a real database for demonstration purposes

const mockPrismaClient = {
  user: {
    findUnique: async () => null,
    create: async (data: any) => ({ id: 'mock-user', ...data.data }),
    findMany: async () => [],
  },
  account: {
    findUnique: async () => null,
    create: async (data: any) => ({ id: 'mock-account', ...data.data }),
  },
  session: {
    findUnique: async () => null,
    create: async (data: any) => ({ id: 'mock-session', ...data.data }),
    delete: async () => ({ id: 'mock-session' }),
    findMany: async () => [],
  },
  verificationToken: {
    findUnique: async () => null,
    create: async (data: any) => ({ identifier: data.data.identifier, token: data.data.token }),
    delete: async () => ({ identifier: 'mock', token: 'mock' }),
  },
  job: {
    create: async (data: any) => ({
      id: `mock-job-${Date.now()}`,
      createdAt: new Date(),
      updatedAt: new Date(),
      ...data.data,
    }),
    findMany: async () => [
      {
        id: 'job-1',
        type: 'digest',
        league: 'NFL',
        status: 'completed',
        result: '{"message":"Mock job completed"}',
        error: null,
        triggeredBy: 'owner@example.com',
        createdAt: new Date(),
        updatedAt: new Date(),
      },
    ],
    update: async (params: any) => ({
      id: params.where.id,
      ...params.data,
    }),
  },
  export: {
    create: async (data: any) => ({
      id: `mock-export-${Date.now()}`,
      createdAt: new Date(),
      ...data.data,
    }),
    findMany: async () => [
      {
        id: 'export-1',
        type: 'google_docs',
        title: 'Sample NFL Digest Export',
        league: 'NFL',
        storyType: 'digest',
        exportedBy: 'owner@example.com',
        externalUrl: 'https://docs.google.com/document/mock',
        metadata: null,
        createdAt: new Date(),
      },
    ],
  },
  auditLog: {
    create: async (data: any) => ({
      id: `mock-audit-${Date.now()}`,
      createdAt: new Date(),
      ...data.data,
    }),
  },
  $disconnect: async () => {},
};

export default mockPrismaClient as any;
