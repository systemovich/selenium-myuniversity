from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException

from datetime import datetime
from sys import stdout
import csv

#-------------------------------------------------------------------------------
# CONSTANTS
#-------------------------------------------------------------------------------

TARGETS = [
	'http://myuniversity.gov.au/UndergraduateCourses',
	'http://myuniversity.gov.au/PostgraduateCourses',
]

COLUMNS = [
	'Course Name',
	'Cut-off ATAR',
	'Duration',
	'Award Type',
	'Field of Education',
	'Provider',
	'Campus',
	'Level',
]

XPATHS = {
	'course_elements': "//div[@class='myuni-small-cell-block']",
    'course_attribute_elements': './/span',
    'next_button': "//div[@class='myuni-alignright-whenbig'][../p[@id='navigationDescriptor']]/a[last()]",
    'number_of_pages': "//div[@class='myuni-alignright-whenbig'][../p[@id='navigationDescriptor']]/label/span[last()]",
}

#-------------------------------------------------------------------------------
# FUNCTIONS
#-------------------------------------------------------------------------------

def create_csv(courses, status):
	timestamp = datetime.today().strftime("%Y-%m-%dT%H-%M-%S")
	file_name = 'myuniversity-courses-' + status + '-' + timestamp  + '.csv'
	print "Writing " + status + " results to ", file_name, ' ...'
	output_file = open(file_name, 'wb')

	dict_writer = csv.DictWriter(output_file, COLUMNS)
	dict_writer.writer.writerow(COLUMNS)
	dict_writer.writerows(courses)

def finish(courses, status):
	create_csv(courses, status)
	if status == 'partial':
		print 'WARNING: Timed-out.'
		print 'Retrying ...'

		# The comma at the end of the print, allows for the page number to appear on the same line.
		# Five spaces between number: and the closing ', prevents the backspaces deleting part of this label.
		print 'Now parsing page number:     ',

	elif status == 'complete':
		print 'Finish time: ', datetime.today().strftime("%H:%M:%S %b %d, %Y")
		print 'Done.'

def get_next_page(driver):
	''' Click the Next link at the bottom of the page.'''
	driver.find_element_by_xpath(XPATHS['next_button']).click()

def parse_page(driver, courses):
	is_undergraduate = TARGETS[0] == driver.current_url
	course_elements = driver.find_elements_by_xpath(XPATHS['course_elements'])
	for course_element in course_elements:
		course_attribute_elements = course_element.find_elements_by_xpath(XPATHS['course_attribute_elements'])
		course = {
			COLUMNS[0]: course_attribute_elements[0].text,
			COLUMNS[1]: course_attribute_elements[2].text if is_undergraduate else '',
			COLUMNS[2]: course_attribute_elements[4].text if is_undergraduate else course_attribute_elements[2].text,
			COLUMNS[3]: course_attribute_elements[5].text if is_undergraduate else course_attribute_elements[3].text,
			COLUMNS[4]: course_attribute_elements[6].text if is_undergraduate else course_attribute_elements[4].text,
			COLUMNS[5]: course_attribute_elements[7].text if is_undergraduate else course_attribute_elements[5].text,
			COLUMNS[6]: course_attribute_elements[8].text if is_undergraduate else course_attribute_elements[6].text,
			COLUMNS[7]: driver.current_url.split('/')[-1].replace('Courses', ''),
		}
		courses.append(course)

def get_backspaces(page_number):
	'''
	To update the current page number in place, the previous number has to be deleted with backspace characters.
	The number of backspaces depends upon the number of digits in the number. Every time the number is divided by 10,
	one of the digits is taken away. In this way, an additional backspace is appended for every digit.
	'''
	n = page_number
	b = "\b"
	while n / 10 > 0:
		b += "\b"
		n /= 10
	return b

def print_page_number(page_number):
	stdout.write(get_backspaces(page_number) + "%d" % page_number)
	stdout.flush()

def has_page_loaded(driver):
	try:
		return 0 == driver.execute_script('return jQuery.active')
	except WebDriverException:
		pass

def parse_all(driver, courses):
	current_page_number = 1
	number_of_pages = int(driver.find_element_by_xpath(XPATHS['number_of_pages']).text.replace('of', ''))

	print 'Total number of pages: ', number_of_pages

	# The comma at the end of the print, allows for the page number to appear on the same line.
	# Five spaces between number: and the closing ', prevents the backspaces deleting part of this label.
	print 'Now parsing page number:     ',

	while number_of_pages >= current_page_number:
		try:
			WebDriverWait(driver, 10).until(has_page_loaded) # Wait for so-many seconds before parsing page.
			print_page_number(current_page_number)
			parse_page(driver, courses)
			current_page_number += 1
			get_next_page(driver) # Click the 'Next' link at the bottom of the page.
		except TimeoutException:
			print
			finish(courses, 'partial')

	print
	driver.quit() # Close browser.

#-------------------------------------------------------------------------------
# EXECUTION
#-------------------------------------------------------------------------------

print 'Start time: ', datetime.today().strftime("%H:%M:%S %b %d, %Y")

courses = []

for TARGET in TARGETS:
	print 'Opening web browser ...'
	browser = webdriver.Firefox()
	print "Visiting: ", TARGET
	browser.get(TARGET)
	parse_all(browser, courses)

finish(courses, 'complete')