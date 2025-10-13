import { MigrationInterface, QueryRunner } from 'typeorm';

export class MergeUserProfile1728518400000 implements MigrationInterface {
  public async up(queryRunner: QueryRunner): Promise<void> {
    // Add new columns to users table
    await queryRunner.query(`
      ALTER TABLE users 
      ADD COLUMN full_name VARCHAR,
      ADD COLUMN lab_role VARCHAR,
      ADD COLUMN preferences JSONB DEFAULT '{}'::jsonb
    `);

    // Migrate data from user_profiles to users if user_profiles table exists
    const hasUserProfiles = await queryRunner.hasTable('user_profiles');
    if (hasUserProfiles) {
      await queryRunner.query(`
        UPDATE users u
        SET 
          full_name = up.full_name,
          lab_role = up.lab_role,
          preferences = up.preferences
        FROM user_profiles up
        WHERE u.id = up.user_id
      `);

      // Drop the user_profiles table
      await queryRunner.query(`DROP TABLE user_profiles`);
    }
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    // Recreate user_profiles table
    await queryRunner.query(`
      CREATE TABLE user_profiles (
        id SERIAL PRIMARY KEY,
        user_id INTEGER UNIQUE NOT NULL,
        full_name VARCHAR,
        lab_role VARCHAR,
        preferences JSONB DEFAULT '{}'::jsonb,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      )
    `);

    // Migrate data back to user_profiles
    await queryRunner.query(`
      INSERT INTO user_profiles (user_id, full_name, lab_role, preferences, created_at, updated_at)
      SELECT id, full_name, lab_role, preferences, created_at, updated_at
      FROM users
      WHERE full_name IS NOT NULL OR lab_role IS NOT NULL OR preferences != '{}'::jsonb
    `);

    // Remove columns from users table
    await queryRunner.query(`
      ALTER TABLE users 
      DROP COLUMN full_name,
      DROP COLUMN lab_role,
      DROP COLUMN preferences
    `);
  }
}
