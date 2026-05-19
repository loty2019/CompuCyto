import { MigrationInterface, QueryRunner } from 'typeorm';

export class RequireImageCaptureMetadata1760000000000 implements MigrationInterface {
  name = 'RequireImageCaptureMetadata1760000000000';

  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`
      DELETE FROM images
      WHERE x_position IS NULL
        OR y_position IS NULL
        OR z_position IS NULL
        OR exposure_time IS NULL
        OR gain IS NULL
        OR gamma IS NULL
        OR file_size IS NULL
        OR width IS NULL
        OR height IS NULL
    `);

    await queryRunner.query(`ALTER TABLE images ALTER COLUMN x_position SET NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN y_position SET NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN z_position SET NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN exposure_time SET NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN gain SET NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN gamma SET NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN file_size SET NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN width SET NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN height SET NOT NULL`);
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN height DROP NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN width DROP NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN file_size DROP NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN gamma DROP NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN gain DROP NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN exposure_time DROP NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN z_position DROP NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN y_position DROP NOT NULL`);
    await queryRunner.query(`ALTER TABLE images ALTER COLUMN x_position DROP NOT NULL`);
  }
}
