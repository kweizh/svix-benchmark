import {
  Controller,
  Post,
  Req,
  HttpCode,
  HttpStatus,
  BadRequestException,
} from '@nestjs/common';
import { Webhook } from 'svix';
import type { Request } from 'express';

@Controller()
export class WebhookController {
  private readonly webhookSecret = 'whsec_MfKQ9r8GffUjCNNdXbn5O6vTmQxOQ9XQ';

  @Post('webhook')
  @HttpCode(HttpStatus.OK)
  handleWebhook(@Req() req: Request): { success: boolean } {
    try {
      // Extract Svix headers
      const svixId = req.headers['svix-id'] as string;
      const svixTimestamp = req.headers['svix-timestamp'] as string;
      const svixSignature = req.headers['svix-signature'] as string;

      if (!svixId || !svixTimestamp || !svixSignature) {
        throw new BadRequestException('Missing required Svix headers');
      }

      // Get the raw body from the request (set by middleware)
      const rawBody = req.rawBody;

      if (!rawBody) {
        throw new BadRequestException('Raw body not available');
      }

      // Verify the webhook signature
      const wh = new Webhook(this.webhookSecret);
      const payload = rawBody.toString('utf8');

      wh.verify(payload, {
        'svix-id': svixId,
        'svix-timestamp': svixTimestamp,
        'svix-signature': svixSignature,
      });

      // If verification succeeds, return 200 OK
      return { success: true };
    } catch {
      // If verification fails, return 400 Bad Request
      throw new BadRequestException('Invalid webhook signature');
    }
  }
}
