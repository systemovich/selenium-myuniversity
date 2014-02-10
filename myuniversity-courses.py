from selenium import webdriver
from time import localtime
import csv

#-------------------------------------------------------------------------------
# CONSTANTS
#-------------------------------------------------------------------------------

TARGET = 'http://myuniversity.gov.au/UndergraduateCourses'

XPATHS = {
	'results_root': "//div[@class='myuni-small-cell-block']",
    'results_leaf': './/span',
    'next_button': "//a[@rel='next']",
    'number_of_pages': "//div[@class='myuni-alignright-whenbig'][../p[@id='navigationDescriptor']]/label/span[last()]",
}

#-------------------------------------------------------------------------------
# FUNCTION DEFINITIONS
#-------------------------------------------------------------------------------

def get_number_of_pages():
	return int(browser.find_element_by_xpath(XPATHS['number_of_pages']).text.replace('of', ''))

def parse_page():
	print 'Parsing web page ...'
	results = browser.find_elements_by_xpath(XPATHS['root'])
	for result in results:
		values = result.find_elements_by_xpath(XPATHS['leaf'])
		course = {
			'Course Name': values[0].text,
			'Cut-off ATAR': values[2].text,
			'Duration': values[4].text,
			'Award Type': values[5].text,
			'Field of Education': values[6].text,
			'Provider': values[7].text,
			'Campus': values[8].text,
		}
		courses.append(course)

def get_timestamp():
	current_time = localtime()
	return '-'.join(map(str, [
		current_time.tm_year,
		current_time.tm_mon,
		current_time.tm_mday,
		current_time.tm_hour,
		current_time.tm_min,
		current_time.tm_sec,
	]))

def create_csv():
	column_names = [
		'Course Name',
		'Cut-off ATAR',
		'Duration',
		'Award Type',
		'Field of Education',
		'Provider',
		'Campus',
	]

	file_name = 'courses-' + get_timestamp() + '.csv'
	print 'Writing results to ', file_name, ' ...'

	output_file = open(file_name, 'wb')
	dict_writer = csv.DictWriter(output_file, column_names)
	dict_writer.writer.writerow(column_names)
	dict_writer.writerows(courses)

#-------------------------------------------------------------------------------
# BEGIN EXECUTION
#-------------------------------------------------------------------------------

print 'Opening web browser ...'
browser = webdriver.Firefox()
browser.get(TARGET)

courses = []
number_of_pages = 1
current_page_number = 1

while True:
	parse_page()
	if number_of_pages != current_page_number:
		current_page_number += 1
		# Visit next page.
	else:
		break

create_csv()
print 'Done.'