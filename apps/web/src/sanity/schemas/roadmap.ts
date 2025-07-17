import { defineField, defineType } from 'sanity';

export const roadmap = defineType({
  name: 'roadmap',
  title: 'Roadmap Section',
  type: 'document',
  fields: [
    defineField({
      name: 'sectionTitle',
      title: 'Section Title',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'timelinePhases',
      title: 'Timeline Phases',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            defineField({
              name: 'phase',
              title: 'Phase',
              type: 'string',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'title',
              title: 'Title',
              type: 'string',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'timeline',
              title: 'Timeline',
              type: 'string',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'status',
              title: 'Status',
              type: 'string',
              options: {
                list: [
                  { title: 'Current', value: 'Current' },
                  { title: 'In Progress', value: 'In Progress' },
                  { title: 'Planned', value: 'Planned' },
                  { title: 'Future', value: 'Future' },
                ],
              },
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'colorClass',
              title: 'Color Class',
              type: 'string',
              description: 'CSS classes for styling (e.g., border-green-400/20 bg-green-400/5)',
            }),
            defineField({
              name: 'features',
              title: 'Features',
              type: 'array',
              of: [{ type: 'string' }],
            }),
          ],
        },
      ],
    }),
    defineField({
      name: 'technologyStack',
      title: 'Technology Stack',
      type: 'object',
      fields: [
        defineField({
          name: 'title',
          title: 'Title',
          type: 'string',
        }),
        defineField({
          name: 'description',
          title: 'Description',
          type: 'text',
        }),
      ],
    }),
  ],
  preview: {
    select: {
      title: 'sectionTitle',
    },
  },
});

export default roadmap;
