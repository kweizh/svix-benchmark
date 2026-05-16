import { Controller, Post, Headers, Req, Res, HttpStatus } from '@nestjs/common';
import { Webhook } from 'svix';

@Controller('webhook')
export class WebhookController {
  private readonly secret = 'whsec_MfKQ9r8GffUjCNNdXbn5O6vTmQxOQ9XQ';

  @Post()
  async handleWebhook(
    @Headers() headers: Record<string, string>,
    @Req() req: any,
    @Res() res: any,
  ) {
    const payload = req.rawBody;

    if (!payload) {
      return res.status(HttpStatus.BAD_REQUEST).send('Missing payload');
    }

    const wh = new Webhook(this.secret);

    try {
      wh.verify(payload, headers);
    } catch (err) {
      console.error('Webhook verification failed:', err);
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid signature');
    }

    return res.status(HttpStatus.OK).send('OK');
  }
}
