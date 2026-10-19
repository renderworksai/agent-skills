'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const parseLines = require('../src/parse');
test('LF rows preserve order', () => assert.deepEqual(parseLines('a\nb'), ['a', 'b']));
test('CRLF rows match LF rows', () => assert.deepEqual(parseLines('a\r\nb'), ['a', 'b']));
test('interior empty rows survive', () => assert.deepEqual(parseLines('a\n\nb'), ['a', '', 'b']));
test('empty input stays one row', () => assert.deepEqual(parseLines(''), ['']));
