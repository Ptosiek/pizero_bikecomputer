# cython: c_string_type=unicode, c_string_encoding=utf8

cdef extern from "logger_fit_c.hpp":
  cdef bint write_log_c(const char* db_file, const char* filename, const char* start_date, const char* end_date, unsigned int unit_id) except +

def write_log_cython(str db_file, str filename, str start_date, str end_date, unsigned int unit_id):
  return write_log_c(db_file, filename, start_date, end_date, unit_id)
