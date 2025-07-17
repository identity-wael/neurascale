import { defineField, defineType } from 'sanity';

export const vision = defineType({
  name: 'vision',
  title: 'Vision Section',
  type: 'document',
  fields: [
    defineField({
      name: 'sectionHeader',
      title: 'Section Header',
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
      name: 'mainStat',
      title: 'Main Statistic',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'mainStatDescription',
      title: 'Main Statistic Description',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'stat1Value',
      title: 'Statistic 1 Value',
      type: 'string',
    }),
    defineField({
      name: 'stat1Label',
      title: 'Statistic 1 Label',
      type: 'string',
    }),
    defineField({
      name: 'stat2Value',
      title: 'Statistic 2 Value',
      type: 'string',
    }),
    defineField({
      name: 'stat2Label',
      title: 'Statistic 2 Label',
      type: 'string',
    }),
    defineField({
      name: 'solutionTitle',
      title: 'Solution Title',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'solutionPoints',
      title: 'Solution Points',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'text',
              title: 'Text',
              type: 'string',
              validation: (Rule) => Rule.required(),
            },
            {
              name: 'highlight',
              title: 'Highlighted Text',
              type: 'string',
              validation: (Rule) => Rule.required(),
            },
          ],
        },
      ],
    }),
    defineField({
      name: 'solutionDescription',
      title: 'Solution Description',
      type: 'text',
    }),
  ],
  preview: {
    select: {
      title: 'title',
    },
  },
});

export default vision;
