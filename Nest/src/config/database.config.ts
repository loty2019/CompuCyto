import { TypeOrmModuleOptions } from '@nestjs/typeorm';
import { ConfigService } from './config.service';

/**
 * Database Configuration Factory
 * 
 * Creates TypeORM configuration for PostgreSQL connection.
 * Used by TypeOrmModule.forRootAsync() in AppModule.
 * 
 * Features:
 * - Auto-loads all entities from **\/*.entity.ts files
 * - Auto-synchronize schema in development (creates/updates tables)
 * - Logging enabled in development for debugging
 * - Migrations support for production deployments
 * 
 * IMPORTANT: synchronize: true should NEVER be used in production!
 * Use migrations instead: npm run migration:generate && npm run migration:run
 * 
 * @param configService - Injectable config service with environment variables
 * @returns TypeORM configuration object
 */
export const getDatabaseConfig = (configService: ConfigService): TypeOrmModuleOptions => ({
  type: 'postgres',                                           // Database type
  host: configService.databaseHost,                          // From DATABASE_HOST env var
  port: configService.databasePort,                          // From DATABASE_PORT env var
  username: configService.databaseUser,                      // From DATABASE_USER env var
  password: configService.databasePassword,                  // From DATABASE_PASSWORD env var
  database: configService.databaseName,                      // From DATABASE_NAME env var
  entities: [__dirname + '/../**/*.entity{.ts,.js}'],       // Auto-load all entities
  synchronize: configService.isDevelopment,                  // DANGER: Only in dev! Auto-creates tables
  logging: configService.isDevelopment,                      // SQL query logging in dev
  migrations: [__dirname + '/../database/migrations/*{.ts,.js}'], // Migration files location
  migrationsRun: false,                                      // Don't auto-run migrations (use npm script)
});
