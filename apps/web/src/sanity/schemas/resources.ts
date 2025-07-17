import { defineField, defineType } from 'sanity';

export const resources = defineType({
  name: 'resources',
  title: 'Resources Section',
  type: 'document',
  fields: [
    defineField({
      name: 'sectionTitle',
      title: 'Section Title',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'introduction',
      title: 'Introduction',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'documentationSections',
      title: 'Documentation Sections',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            defineField({
              name: 'title',
              title: 'Title',
              type: 'string',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'description',
              title: 'Description',
              type: 'text',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'iconType',
              title: 'Icon Type',
              type: 'string',
              options: {
                list: [
                  { title: 'Rocket', value: 'rocket' },
                  { title: 'Book', value: 'book' },
                  { title: 'Code', value: 'code' },
                  { title: 'Users', value: 'users' },
                ],
              },
            }),
            defineField({
              name: 'resources',
              title: 'Resources',
              type: 'array',
              of: [{ type: 'string' }],
            }),
          ],
        },
      ],
    }),
    defineField({
      name: 'researchPapers',
      title: 'Research Papers',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            defineField({
              name: 'title',
              title: 'Title',
              type: 'string',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'authors',
              title: 'Authors',
              type: 'string',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'summary',
              title: 'Summary',
              type: 'text',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'category',
              title: 'Category',
              type: 'string',
            }),
            defineField({
              name: 'pages',
              title: 'Pages',
              type: 'string',
            }),
            defineField({
              name: 'date',
              title: 'Date',
              type: 'string',
            }),
            defineField({
              name: 'url',
              title: 'URL',
              type: 'url',
            }),
          ],
        },
      ],
    }),
    defineField({
      name: 'externalReferences',
      title: 'External References',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            defineField({
              name: 'title',
              title: 'Title',
              type: 'string',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'description',
              title: 'Description',
              type: 'text',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'url',
              title: 'URL',
              type: 'url',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'displayUrl',
              title: 'Display URL',
              type: 'string',
            }),
            defineField({
              name: 'category',
              title: 'Category',
              type: 'string',
            }),
          ],
        },
      ],
    }),
  ],
  preview: {
    select: {
      title: 'sectionTitle',
    },
  },
});

export default resources;
