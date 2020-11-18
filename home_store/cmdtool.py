from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime
from home_store.helpers import populate, sparse, database


def check_period(value):
	for pattern in ['%Y-%m-%d', '%Y-%m']:
		try:
			datetime.strptime(value, pattern)
			return value
		except:
			continue
	raise ArgumentTypeError('%s is not a valid period. ' \
		'Valid formats are 2020-10 for month or 2020-10-01 for date.' % value)


if __name__ == '__main__':
	parser = ArgumentParser()
	subparsers = parser.add_subparsers(help='sub-command help', dest='action')
	subparsers.required = True

	parser_c = subparsers.add_parser('init', 
		help='Creates the database file with all its defined tables.')
	parser_e = subparsers.add_parser('drop', 
		help='Removes all entries or for a given sensor.')

	parser_a = subparsers.add_parser('sparse', 
		help='Sparse database entries for a given sensor.')
	parser_a.add_argument('name', 
		help='Name of the sensor to remove entries for.')
	parser_a.add_argument('period', type=check_period, 
		help='entries will be sparsed from this period, ' \
		'i.e. month (2020-10) of date (2020-10-01')

	parser_b = subparsers.add_parser('populate', 
		help='Add database entries with random values.')
	parser_b.add_argument('name', 
		help='name of the sensor to simulate entries for')
	parser_b.add_argument('count', type=int, 
		help='number of entries to generate per day')
	parser_b.add_argument('period', type=check_period, 
		help='entries will be generated for this period, ' \
		'i.e. month (2020-10) of date (2020-10-01')

	args = parser.parse_args()

	if args.action == 'sparse':
		sparse.sparse_period(args.name, args.period)
	if args.action == 'populate':
		populate.create_for_period(args.name, args.period, args.count)
	if args.action == 'init':
		database.create()
	if args.action == 'drop':
		database.drop()
		