import { MigrationInterface, QueryRunner, TableColumn } from "typeorm";

export class AddGammaToImages1760743671998 implements MigrationInterface {

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.addColumn('images', new TableColumn({
            name: 'gamma',
            type: 'float',
            isNullable: true,
        }));
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.dropColumn('images', 'gamma');
    }

}
