import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  OnGatewayInit,
  OnGatewayConnection,
  OnGatewayDisconnect,
  MessageBody,
  ConnectedSocket,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { Logger } from '@nestjs/common';

/**
 * WebSocket Gateway for real-time communication
 *
 * Provides real-time updates for:
 * - Camera status and image capture events
 * - Stage position updates
 * - Job progress notifications
 * - System health status changes
 */
@WebSocketGateway({
  cors: {
    origin: ['http://localhost:5173', 'http://localhost:3000'],
    credentials: true,
  },
})
export class EventsGateway
  implements OnGatewayInit, OnGatewayConnection, OnGatewayDisconnect
{
  @WebSocketServer()
  server: Server;

  private logger: Logger = new Logger('EventsGateway');

  /**
   * Called when the gateway is initialized
   */
  afterInit(_server: Server) {
    this.logger.log('WebSocket Gateway initialized');
  }

  /**
   * Called when a client connects
   */
  handleConnection(client: Socket) {
    this.logger.log(`Client connected: ${client.id}`);

    // Send initial connection confirmation
    client.emit('status', {
      type: 'status',
      data: {
        connected: true,
        timestamp: new Date().toISOString(),
      },
    });
  }

  /**
   * Called when a client disconnects
   */
  handleDisconnect(client: Socket) {
    this.logger.log(`Client disconnected: ${client.id}`);
  }

  /**
   * Handle echo messages (for testing connection)
   */
  @SubscribeMessage('echo')
  handleEcho(@MessageBody() data: any, @ConnectedSocket() client: Socket): any {
    this.logger.debug(`Echo from ${client.id}: ${JSON.stringify(data)}`);
    return {
      type: 'echo',
      data: data,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Broadcast position update to all connected clients
   */
  broadcastPositionUpdate(position: { x: number; y: number; z: number }) {
    this.server.emit('message', {
      type: 'position',
      data: position,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Broadcast job progress update to all connected clients
   */
  broadcastJobProgress(jobData: {
    job_id: string;
    progress: number;
    total_steps: number;
    status: string;
  }) {
    this.server.emit('message', {
      type: 'job_progress',
      data: jobData,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Broadcast image captured event to all connected clients
   */
  broadcastImageCaptured(imageData: { filename: string; path: string }) {
    this.server.emit('message', {
      type: 'image_captured',
      data: imageData,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Broadcast system status update to all connected clients
   */
  broadcastStatusUpdate(status: {
    camera?: string;
    stage?: string;
    database?: string;
    raspberryPi?: string;
  }) {
    this.server.emit('message', {
      type: 'status',
      data: status,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Broadcast error to all connected clients
   */
  broadcastError(error: { component: string; message: string }) {
    this.server.emit('message', {
      type: 'error',
      data: error,
      timestamp: new Date().toISOString(),
    });
  }
}
