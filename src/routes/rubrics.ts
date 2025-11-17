import { FastifyInstance } from 'fastify';
import { RubricService } from '../services/RubricService';
import { authenticateJWT, requirePermission } from '../middleware/auth';
import { Permission } from '../types';

export async function rubricRoutes(fastify: FastifyInstance) {
  const service = new RubricService();

  // List all rubrics
  fastify.get(
    '/api/rubrics',
    {
      preHandler: [authenticateJWT, requirePermission(Permission.RUBRIC_READ)],
    },
    async (request, reply) => {
      const rubrics = await service.listRubrics();
      return { rubrics };
    }
  );

  // Create custom rubric
  fastify.post(
    '/api/rubrics',
    {
      preHandler: [authenticateJWT, requirePermission(Permission.RUBRIC_WRITE)],
    },
    async (request, reply) => {
      const body = request.body as any;
      const rubric = await service.createRubric({
        ...body,
        created_by: request.user!.user_id,
      });

      return rubric;
    }
  );

  // Update rubric
  fastify.patch(
    '/api/rubrics/:id',
    {
      preHandler: [authenticateJWT, requirePermission(Permission.RUBRIC_WRITE)],
    },
    async (request, reply) => {
      const { id } = request.params as { id: string };
      const body = request.body as any;
      const rubric = await service.updateRubric(id, body);

      return rubric;
    }
  );

  // Reorder rubrics
  fastify.post(
    '/api/rubrics/reorder',
    {
      preHandler: [authenticateJWT, requirePermission(Permission.RUBRIC_WRITE)],
    },
    async (request, reply) => {
      const { order } = request.body as { order: string[] };
      await service.reorderRubrics(order);

      return { success: true };
    }
  );

  // Validate weights
  fastify.get(
    '/api/rubrics/validate',
    {
      preHandler: [authenticateJWT, requirePermission(Permission.RUBRIC_READ)],
    },
    async (request, reply) => {
      const validation = await service.validateWeights();
      return validation;
    }
  );
}
