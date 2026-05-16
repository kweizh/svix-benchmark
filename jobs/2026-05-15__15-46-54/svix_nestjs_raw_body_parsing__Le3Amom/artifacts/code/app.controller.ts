import { Controller, Get, Post, Req, Res, HttpStatus } from '@nestjs/common';
import type { RawBodyRequest } from '@nestjs/common';
import { AppService } from './app.service';
import { Webhook } from 'svix';
import type { Request, Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getHello(): string {
    return this.appService.getHello();
  }

  @Post('webhook')
  async handleWebhook(@Req() req: RawBodyRequest<Request>, @Res() res: Response) {
    const secret = 'whsec_MfKQ9r8GffUjCNNdXbn5O6vTmQxOQ9XQ';
    const webhook = new Webhook(secret);

    const payload = req.rawBody?.toString('utf8');
    const headers = req.headers;

    if (!payload) {
      return res.status(HttpStatus.BAD_REQUEST).send('Missing payload');
    }

    try {
      webhook.verify(payload, headers as any);
      return res.status(HttpStatus.OK).send('Success');
    } catch (err) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid signature');
    }
  }
}
