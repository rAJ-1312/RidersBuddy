import click
from app.db.database import SessionLocal, neo4j_driver
from app.factory import GridFactory, RiderFactory


@click.group()
def cli():
    pass


@cli.command()
@click.option("--waypoints", default=500, help="Number of waypoints to create")
@click.option("--riders", default=20, help="Number of riders to create")
def seed(waypoints: int, riders: int):
    pg_db = SessionLocal()
    neo4j_db = neo4j_driver.session()

    try:
        click.echo(f"Creating {waypoints} waypoints on grid...")
        grid_factory = GridFactory(pg_db, neo4j_db)
        created_waypoints = grid_factory.populate_grid(count=waypoints)
        click.echo(f"✓ Created {len(created_waypoints)} waypoints")

        click.echo(f"Creating {riders} riders...")
        rider_factory = RiderFactory(pg_db, neo4j_db)
        created_riders = rider_factory.create_riders(count=riders)
        click.echo(f"✓ Created {len(created_riders)} riders")

        click.echo("Database seeding complete!")
    finally:
        pg_db.close()
        neo4j_db.close()


if __name__ == "__main__":
    cli()
